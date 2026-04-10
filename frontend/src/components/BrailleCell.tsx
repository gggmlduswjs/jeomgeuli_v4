/**
 * 점자 셀 렌더링
 *
 * pattern: [p1, p2, p3, p4, p5, p6]
 * 실제 점자 배치:
 *     1 4
 *     2 5
 *     3 6
 */
type Props = {
  pattern: number[];
  size?: "sm" | "md" | "lg";
  label?: string;
};

export default function BrailleCell({ pattern, size = "md", label }: Props) {
  // grid 순서로 재배치: (1,4)(2,5)(3,6) → 배열 인덱스 [0,3,1,4,2,5]
  const gridOrder = [0, 3, 1, 4, 2, 5];

  const sizeClasses = {
    sm: { cell: "w-10 h-14 p-1 gap-1", dot: "w-3 h-3" },
    md: { cell: "w-16 h-24 p-2 gap-2", dot: "w-5 h-5" },
    lg: { cell: "w-24 h-36 p-3 gap-3", dot: "w-8 h-8" },
  }[size];

  return (
    <div className="flex flex-col items-center">
      <div
        className={`grid grid-cols-2 grid-rows-3 bg-white border border-gray-400 rounded-xl shadow ${sizeClasses.cell}`}
      >
        {gridOrder.map((idx) => (
          <div
            key={idx}
            className={`rounded-full transition-all ${sizeClasses.dot} ${
              pattern[idx] ? "bg-black" : "bg-gray-200"
            }`}
          />
        ))}
      </div>
      {label && <span className="mt-1 text-xs text-gray-500">{label}</span>}
    </div>
  );
}
